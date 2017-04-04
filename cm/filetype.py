import os, mimetypes


def guess_file_type(path):
    '''Returns a string of the content-type of the file by
    guessing from the file extension.
    '''
    guess_mime, guess_enc = mimetypes.guess_type(os.path.basename(path),
                                                 strict=0)
    #self.encoding = guess_enc or None
    return guess_mime or 'text/plain'


